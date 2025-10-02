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
  CreateInvalidationRequest,
  CreateInvalidationResult,
} from "../models/models_0";
export { __MetadataBearer, $Command };
export interface CreateInvalidationCommandInput
  extends CreateInvalidationRequest {}
export interface CreateInvalidationCommandOutput
  extends CreateInvalidationResult,
    __MetadataBearer {}
export declare class CreateInvalidationCommand extends $Command<
  CreateInvalidationCommandInput,
  CreateInvalidationCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: CreateInvalidationCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: CreateInvalidationCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<CreateInvalidationCommandInput, CreateInvalidationCommandOutput>;
  private serialize;
  private deserialize;
}
