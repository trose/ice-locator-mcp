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
  CreateFieldLevelEncryptionProfileRequest,
  CreateFieldLevelEncryptionProfileResult,
} from "../models/models_0";
export { __MetadataBearer, $Command };
export interface CreateFieldLevelEncryptionProfileCommandInput
  extends CreateFieldLevelEncryptionProfileRequest {}
export interface CreateFieldLevelEncryptionProfileCommandOutput
  extends CreateFieldLevelEncryptionProfileResult,
    __MetadataBearer {}
export declare class CreateFieldLevelEncryptionProfileCommand extends $Command<
  CreateFieldLevelEncryptionProfileCommandInput,
  CreateFieldLevelEncryptionProfileCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: CreateFieldLevelEncryptionProfileCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: CreateFieldLevelEncryptionProfileCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    CreateFieldLevelEncryptionProfileCommandInput,
    CreateFieldLevelEncryptionProfileCommandOutput
  >;
  private serialize;
  private deserialize;
}
