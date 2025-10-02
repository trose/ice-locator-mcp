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
import {
  GetKeyGroupConfigRequest,
  GetKeyGroupConfigResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetKeyGroupConfigCommandInput
  extends GetKeyGroupConfigRequest {}
export interface GetKeyGroupConfigCommandOutput
  extends GetKeyGroupConfigResult,
    __MetadataBearer {}
export declare class GetKeyGroupConfigCommand extends $Command<
  GetKeyGroupConfigCommandInput,
  GetKeyGroupConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetKeyGroupConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetKeyGroupConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<GetKeyGroupConfigCommandInput, GetKeyGroupConfigCommandOutput>;
  private serialize;
  private deserialize;
}
