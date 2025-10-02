import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import { GetKeyGroupRequest, GetKeyGroupResult } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetKeyGroupCommandInput extends GetKeyGroupRequest {}
export interface GetKeyGroupCommandOutput
  extends GetKeyGroupResult,
    __MetadataBearer {}
export declare class GetKeyGroupCommand extends $Command<
  GetKeyGroupCommandInput,
  GetKeyGroupCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetKeyGroupCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetKeyGroupCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<GetKeyGroupCommandInput, GetKeyGroupCommandOutput>;
  private serialize;
  private deserialize;
}
